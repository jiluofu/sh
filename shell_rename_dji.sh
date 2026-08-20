# rename -n 's/DJI_[\d]{1,}_//' $1/*.WAV
rename 's/DJI_[\d]{1,}_//' $1/*.WAV
rename -n 's/\[P\d{3}\]//g' *
rename 's/\[P\d{3}\]//g' *.WAV