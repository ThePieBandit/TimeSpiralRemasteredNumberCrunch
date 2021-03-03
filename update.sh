#!/bin/sh

cd src/assets
python3 numbercrunch.py
cd  ../..
ng build --prod=true --outputPath=docs --base-href=/TimeSpiralRemasteredNumberCrunch/
git add .
git commit -m"Updating site"
git push
