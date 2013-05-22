#!/bin/sh

ROOT_PATH=$PWD
TOOLS="$ROOT_PATH/tools"
BASELINE="$ROOT_PATH/baseline"
CORPUS="$BASELINE/corpus"
LM="$BASELINE/lm"
WORK="$BASELINE/working"
GIZAPP="$TOOLS/bin"
export IRSTLM="$TOOLS/irstlm"
MOSES="$TOOLS/moses"



mkdir $BASELINE
mkdir $CORPUS
mkdir $LM
mkdir $WORK



cd $CORPUS

export IRSTLM="$TOOLS/irstlm"


# get dataset
curl -O http://www.statmt.org/wmt12/training-parallel.tgz
tar xzvf training-parallel.tgz

# tokenization
$MOSES/scripts/tokenizer/tokenizer.perl -l en < $CORPUS/training/news-commentary-v7.fr-en.en > $CORPUS/news-commentary-v7.fr-en.tok.en
$MOSES/scripts/tokenizer/tokenizer.perl -l fr < $CORPUS/training/news-commentary-v7.fr-en.fr > $CORPUS/news-commentary-v7.fr-en.tok.fr

# truecasing
$MOSES/scripts/recaser/train-truecaser.perl --model $CORPUS/truecase-model.en --corpus $CORPUS/news-commentary-v7.fr-en.tok.en
$MOSES/scripts/recaser/train-truecaser.perl --model $CORPUS/truecase-model.fr --corpus $CORPUS/news-commentary-v7.fr-en.tok.fr
$MOSES/scripts/recaser/truecase.perl --model $CORPUS/truecase-model.en < $CORPUS/news-commentary-v7.fr-en.tok.en > $CORPUS/news-commentary-v7.fr-en.true.en
$MOSES/scripts/recaser/truecase.perl --model $CORPUS/truecase-model.fr < $CORPUS/news-commentary-v7.fr-en.tok.fr > $CORPUS/news-commentary-v7.fr-en.true.fr

# cleaning
$MOSES/scripts/training/clean-corpus-n.perl $CORPUS/news-commentary-v7.fr-en.true fr en $CORPUS/news-commentary-v7.fr-en.clean 1 80



# language model training
cd $LM
$IRSTLM/bin/add-start-end.sh < $CORPUS/news-commentary-v7.fr-en.true.en > news-commentary-v7.fr-en.sb.en
$IRSTLM/bin/build-lm.sh -i news-commentary-v7.fr-en.sb.en -t ./tmp -p -s improved-kneser-ney -o news-commentary-v7.fr-en.lm.en
$IRSTLM/bin/compile-lm --text yes news-commentary-v7.fr-en.lm.en.gz news-commentary-v7.fr-en.arpa.en

$MOSES/bin/build_binary news-commentary-v7.fr-en.arpa.en news-commentary-v7.fr-en.blm.en
echo "is this an English sentence ?" | $MOSES/bin/query news-commentary-v7.fr-en.blm.en



# training translation system
cd $WORK

nohup nice $MOSES/scripts/training/train-model.perl -root-dir train -corpus $CORPUS/news-commentary-v7.fr-en.clean -f fr -e en -alignment grow-diag-final-and -reordering msd-bidirectional-fe -lm 0:3:$LM/news-commentary-v7.fr-en.blm.en:8 -external-bin-dir $GIZAPP -mgiza > training.out 2>&1



# tuning
cd $CORPUS
curl -O http://www.statmt.org/wmt12/dev.tgz
tar xzvf dev.tgz

$MOSES/scripts/tokenizer/tokenizer.perl -l en < dev/news-test2008.en > news-test2008.tok.en
$MOSES/scripts/tokenizer/tokenizer.perl -l fr < dev/news-test2008.fr > news-test2008.tok.fr
$MOSES/scripts/recaser/truecase.perl --model truecase-model.en < news-test2008.tok.en > news-test2008.true.en
$MOSES/scripts/recaser/truecase.perl --model truecase-model.fr < news-test2008.tok.fr > news-test2008.true.fr

cd $WORK
nohup nice $MOSES/scripts/training/mert-moses.pl $CORPUS/news-test2008.true.fr $CORPUS/news-test2008.true.en $MOSES/bin/moses  train/model/moses.ini --mertdir $MOSES/bin/ --decoder-flags="-threads 8" > mert.out 2>&1
