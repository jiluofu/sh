echo $1;
rm -rf $1/output;
mkdir $1/output;
echo "output:"$1
echo "resize photos"
cd $1
find . -type f -name "*.jpg"|xargs -I {} convert -resize 600x600 {} output/{}
echo "compress photos"
cd output
find . -type f -name "*.jpg"|xargs -I {} jpegoptim  -m90 {}


