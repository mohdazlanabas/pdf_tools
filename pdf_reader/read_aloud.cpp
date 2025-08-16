#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <cstdlib>
#include <thread>
#include <atomic>
#include <chrono>

// Atomic flag to check if user pressed 'z'
std::atomic<bool> stop_requested(false);

// Background thread function to listen for 'z' key
void listen_for_stop() {
    while (!stop_requested) {
        char ch = getchar();
        if (ch == 'z' || ch == 'Z') {
            stop_requested = true;
            std::cout << "\n'z' pressed. Stopping...\n";
            break;
        }
    }
}

// Speak function: handles chunking and cross-platform TTS
void speak(const std::string &text) {
    const size_t chunk_size = 500; // Max chars per chunk to avoid TTS choke

    for (size_t i = 0; i < text.size(); i += chunk_size) {
        if (stop_requested) break; // Stop if 'z' pressed

        std::string chunk = text.substr(i, chunk_size);

#if defined(_WIN32) || defined(_WIN64)
        std::string command = "powershell -Command \"Add-Type -AssemblyName System.Speech; "
                              "$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                              "$speak.Speak(\\\"" + chunk + "\\\")\"";
#elif defined(__APPLE__)
        std::string command = "say \"" + chunk + "\"";
#else
        std::string command = "espeak \"" + chunk + "\"";
#endif

        std::cout << "Speaking chunk...\n";
        system(command.c_str());

        // Small pause between chunks
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

int main() {
    std::ifstream file("HD_output.txt");
    if (!file.is_open()) {
        std::cerr << "Error: Could not open HD_output.txt" << std::endl;
        return 1;
    }

    // Read entire file into one string
    std::ostringstream ss;
    ss << file.rdbuf();
    std::string content = ss.str();

    if (content.empty()) {
        std::cerr << "Error: HD_output.txt is empty." << std::endl;
        return 1;
    }

    std::cout << "Reading text aloud... (Press 'z' to stop)\n";

    // Start key listener thread
    std::thread stop_thread(listen_for_stop);

    // Start speaking
    speak(content);

    stop_requested = true; // Just in case
    stop_thread.join();

    if (stop_requested) {
        std::cout << "Reading stopped by user.\n";
    } else {
        std::cout << "Done reading.\n";
    }

    return 0;
}
