#!/bin/bash

echo -e "\033[0;32mUpdating blog repository...\033[0m"

# Add changes to git.
git add .

# Commit changes.
msg="updated the blog rep on `date`"
if [ $# -eq 1 ]
  then msg="$1"
fi
git commit -m "$msg"

# Push source and build repos.
git push origin master


