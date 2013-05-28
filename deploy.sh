#!/bin/sh

TOOLS="$PWD/tools"
SAMPLE="$PWD/sample"
GIZAPP="$TOOLS/bin"
MGIZAPP="$TOOLS/mgizapp"
IRSTLM="$TOOLS/irstlm"
MOSES="$TOOLS/moses"

# Install dependencies
sudo apt-get install build-essential curl libboost-all-dev cmake autotools-dev libtool git-core automake zlib1g zlib1g-dev libbz2-dev


mkdir $TOOLS
mkdir $SAMPLE
mkdir $GIZAPP
mkdir $MGIZAPP



# GIZA++
cd $TOOLS
curl -O https://giza-pp.googlecode.com/files/giza-pp-v1.0.7.tar.gz
tar xzvf giza-pp-v1.0.7.tar.gz
cd giza-pp
make
cp $PWD/GIZA++-v2/GIZA++ $GIZAPP
cp $PWD/GIZA++-v2/snt2cooc.out $GIZAPP
cp $PWD/mkcls-v2/mkcls $GIZAPP



# MGIZA++
curl -O http://hivelocity.dl.sourceforge.net/project/mgizapp/mgizapp-0.7.3.tgz
tar xzvf mgizapp-0.7.3.tgz
mv mgizapp mgizapp-src
cd mgizapp-src
rm CMakeCache.txt
cmake -DCMAKE_INSTALL_PREFIX=$MGIZAPP
make
make install
cp $MGIZAPP/bin/mgiza $GIZAPP/mgizapp
cp $MGIZAPP/scripts/merge_alignment.py $GIZAPP



# IRSTLM
cd $TOOLS
curl -O http://hivelocity.dl.sourceforge.net/project/irstlm/irstlm/irstlm-5.80/irstlm-5.80.01.tgz
tar xzvf irstlm-5.80.01.tgz
cd irstlm-5.80.01
sh regenerate-makefiles.sh --force
./configure --prefix=$IRSTLM
make
make install



# Moses
cd $TOOLS
git clone git://github.com/moses-smt/mosesdecoder.git moses
cd moses
./bjam --j8 --with-irstlm=$IRSTLM



cd $SAMPLE
curl -O http://www.statmt.org/moses/download/sample-models.tgz
tar xzvf sample-models.tgz
cd sample-models
# modify moses.ini to use IRSTLM
perl -pi.bak -e "s|8(?= 0 3 lm/europarl.srilm.gz)|1|" phrase-model/moses.ini
$MOSES/bin/moses -f phrase-model/moses.ini < phrase-model/in > out
cat out
