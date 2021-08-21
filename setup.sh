if ! command -v poetry &> /dev/null
then
    echo "Poetry not found, installing from pip..."
    pip install poetry
else
    echo "Poetry is already installed, you're good to go!"
fi
