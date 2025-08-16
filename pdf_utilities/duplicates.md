

SHOW DUPLICATES

find ~/Documents -type f -iname "*.pdf" -exec basename {} \; \
| awk '{print tolower($0)}' \
| sort | uniq -d | while read name; do
  echo "---- $name ----"
  find ~/Documents -type f -iname "$name" -exec stat -f "%N %Sm" -t "%Y-%m-%d %H:%M" {} \; \
  | awk -F'/' '{print $NF}'
done

SHOW DUPLCATES TO BE DELETED

find ~/Documents -type f -iname "*.pdf" -exec basename {} \; \
| awk '{print tolower($0)}' \
| sort | uniq -d | while read name; do
  echo "---- $name ----"
  find ~/Documents -type f -iname "$name" -printf "%T@ %p\n" \
  | sort -nr \
  | awk 'NR>2 {print "DELETE:", $2}'
done

DELETE DUPLICATE

find ~/Documents -type f -iname "*.pdf" -exec basename {} \; \
| awk '{print tolower($0)}' \
| sort | uniq -d | while read name; do
  echo "---- $name ----"
  find ~/Documents -type f -iname "$name" -printf "%T@ %p\n" \
  | sort -nr \
  | awk 'NR>2 {print "Deleting:", $2; system("rm -v \""$2"\"")}'
done

FIND SPECIFIC MATCHING FILE AND AND ITS DUPLICATE WITH PATH

find . -type f -iname "FILENAME" | fzf --multi | while read -r file; do
  name=$(basename "$file" | awk '{print tolower($0)}')
  echo "---- Duplicates of $name ----"
  find . -type f -iname "$name"
done

DELETE SPECIFIC FILE

rm -i /full/path/to/your/FILENAME.EXTENSION

CHECK FOLDER NAME HAS “-“

find ~/Documents -type d -name "*-*"

RENAME FOLDERS THAT HAVE - to _

find ~/Documents -depth -type d -name "*-*" | while read -r dir; do
  newname="$(dirname "$dir")/$(basename "$dir" | tr '-' '_')"
  echo "Renaming: $dir -> $newname"
  mv -v "$dir" "$newname"
done
