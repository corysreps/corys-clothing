#!/usr/bin/env bash

# Posodobi pip, setuptools in wheel
echo "🔧 Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

# Namesti sistemske pakete (če uporabljaš build za Python z buildpakom)
# Primer: če paket potrebuje libpq-dev, libxml2-dev itd.
# apt-get ukazi delujejo le, če uporabljaš Docker ali imaš poseben buildpak, sicer jih izpusti!

# echo "📦 Installing system dependencies..."
# apt-get update && apt-get install -y build-essential libpq-dev

# Namesti Python odvisnosti iz requirements.txt
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
