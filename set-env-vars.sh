export TAL_FOLDER_PATH=$PWD

#+--------------------------------------+
#| python virtual environment variables |
#+--------------------------------------+

export TAL_VENV_FOLDER_PATH=$TAL_FOLDER_PATH/tal-virtual-env
export TAL_VENV_ACTIVATE_FILE_PATH=$TAL_VENV_FOLDER_PATH/env/bin/activate

#+------------------+
#| python variables |
#+------------------+

export LC_ALL=C
export PYTHONIOENCODING=utf-8

#+---------------+
#| PATH variable |
#+---------------+

if [[ ! $PATH =~ $TAL_FOLDER_PATH ]]
then
    PATH=$PATH:$TAL_FOLDER_PATH
fi


