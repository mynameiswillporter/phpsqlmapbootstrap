# PHP sqlmap Bootstrap
This program functions by parsing php files for query string parameters and generating urls
containing those parameters to pass into sqlmap. This is an automated way to generate better
guesses with sqlmap. It isn't perfect because it doesn't do any path analysis to determine sane
values for the parameters, but is better than sqlmap by itself.

```
-h      --help                  Display this message
-u      --url                   A base url for the web application being tested
-o      --output-file           The filename to output the .sh script
-d      --output-directory      The directory to store the .sh script in
-p      --php-root-directory    The directory where the php application sits
```