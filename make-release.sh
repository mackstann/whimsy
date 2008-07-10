die () {
    echo "$1" >&2
    exit 1;
}

echo -n "what should i call this release? "
read release

set -x

git status | fgrep -q 'nothing to commit (working directory clean)' || die "unclean working directory"

find tests -name '*.py' | while read i
do
    python "$i" || die "you have failing tests, loser"
done

echo "all tests passed"

git tag -m "$release" || die "git tag failed"

dir=whimsy-"$release"

cp -a . "$dir"
rm -rf "$dir"/Xlib
find "$dir" -name '*.pyc' | while read i; do rm -f "$i"; done

tar zcvf "$dir".tgz "$dir"

