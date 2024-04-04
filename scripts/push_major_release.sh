# 0. determine the project root, which is ./../../.. relative to this script
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )/.."
# 0.1 modify setup.py to increase minor version
cd "$PROJECT_ROOT" || exit
# use sed to replace the version number. The version part is like version="a.b.c"
# the current minor is the c part
CURRENT_MINOR=$(grep -oP '(?<=version=")[^"]*' setup.py | cut -d. -f3)
CURRENT_MAJOR=$(grep -oP '(?<=version=")[^"]*' setup.py | cut -d. -f1)
CURRENT_SECONDARY=$(grep -oP '(?<=version=")[^"]*' setup.py | cut -d. -f2)
# then increment it
NEW_MAJOR=$((CURRENT_MAJOR+1))
NEW_MINOR=0
NEW_SECONDARY=0
# then replace it, keeping the original a and b parts
sed -i "s/version=\"${CURRENT_MAJOR}.${CURRENT_SECONDARY}.${CURRENT_MINOR}\"/version=\"${NEW_MAJOR}.${NEW_SECONDARY}.${NEW_MINOR}\"/g" setup.py
# 1. do git add and git commit
git add .
NEW_VERSION="${NEW_MAJOR}.${NEW_SECONDARY}.${NEW_MINOR}"
git commit -m "release: -> v$NEW_VERSION"
# tag it
git tag "v${NEW_MAJOR}.${NEW_SECONDARY}.${NEW_MINOR}"
# 2. do git push
git push
git push --tags

# print a.b.c  -> new a.b.c
echo "v${CURRENT_MAJOR}.${CURRENT_SECONDARY}.${CURRENT_MINOR} -> v${NEW_MAJOR}.${NEW_SECONDARY}.${NEW_MINOR}"