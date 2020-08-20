cwd=$PWD
target="${cwd}/eu_parliament"
linkname="${cwd}/nbs/eu_parliament"
echo "Setting link to $target from $linkname"
ln -s $target $linkname
