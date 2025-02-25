#!/bin/bash

download_data() {
    local url=$1
    local zipfile=$2
    local target=$3

    if [ -e "$target" ]; then
        echo "$target already exists, skipping."
    else
        wget $url -O "${zipfile}.zip"
        unzip "${zipfile}.zip"
        mv $zipfile $target
        rm "${zipfile}.zip"
    fi
}

# Create folders

mkdir -p ./data
cd ./data

rm -rf ./combined

mkdir -p ./download
mkdir -p ./combined/sock-shop
mkdir -p ./combined/online-boutique
mkdir -p ./combined/train-ticket

cd ./download

# Download datasets from zenodo

download_data https://zenodo.org/records/11046533/files/fse-ss.zip?download=1 fse-ss sock-shop-baro
download_data https://zenodo.org/records/11046533/files/fse-ob.zip?download=1 fse-ob online-boutique-baro
download_data https://zenodo.org/records/11046533/files/fse-tt.zip?download=1 fse-tt train-ticket-baro
download_data https://zenodo.org/records/13305663/files/sock-shop-1.zip?download=1 sock-shop-1 sock-shop-rcd
download_data https://zenodo.org/records/13305663/files/sock-shop-2.zip?download=1 sock-shop-2 sock-shop-rca-eval
download_data https://zenodo.org/records/13305663/files/online-boutique.zip?download=1 online-boutique online-boutique-rca-eval
download_data https://zenodo.org/records/13305663/files/train-ticket.zip?download=1 train-ticket train-ticket-rca-eval

cd ..

# copy BARO datasets to combined

cp -R ./download/sock-shop-baro ./combined/sock-shop/sock-shop-baro
cp -R ./download/online-boutique-baro ./combined/online-boutique/online-boutique-baro
cp -R ./download/train-ticket-baro ./combined/train-ticket/train-ticket-baro

# copy RCD dataset to combined

cp -R ./download/sock-shop-rcd/sock-shop ./combined/sock-shop/sock-shop-rcd

# copy RCA-Eval datasets to combined

mkdir -p ./combined/sock-shop/sock-shop-rca-eval
cp -R ./download/sock-shop-rca-eval/*_disk ./combined/sock-shop/sock-shop-rca-eval/

mkdir -p  ./combined/online-boutique/online-boutique-rca-eval
cp -R ./download/online-boutique-rca-eval/*_cpu ./combined/online-boutique/online-boutique-rca-eval/
cp -R ./download/online-boutique-rca-eval/*_mem ./combined/online-boutique/online-boutique-rca-eval/
cp -R ./download/online-boutique-rca-eval/*_disk ./combined/online-boutique/online-boutique-rca-eval/
cp -R ./download/online-boutique-rca-eval/adservice_* ./combined/online-boutique/online-boutique-rca-eval/

mkdir -p ./combined/train-ticket/train-ticket-rca-eval
cp -R ./download/train-ticket-rca-eval/*_disk ./combined/train-ticket/train-ticket-rca-eval/

# Rename simple versions to right format

find ./combined/sock-shop/sock-shop-rcd -type f -name "data.csv" -execdir mv {} simple_data.csv \;
find ./combined/online-boutique/online-boutique-rca-eval -type f -name "data.csv" -execdir mv {} simple_data.csv \;
