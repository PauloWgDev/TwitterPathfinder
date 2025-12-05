# Twitter Mentions Network

On this project we use mentions on twitter posts to generate a network of accounts. From that we generated an accounts pathfinder, it shows the sequence of accounts that you would need to traverse to get from account A to account B using only mentions.

## Getting Data

In order to get the data we made a twitter scrapper script `TwitterScrapper.py`. It goes through different twitter profiles and searches for mentions, when it finds a mention it stores it at an array and then proceeds to analyze the accounts it has it that array.

## Network Graph

![image](https://github.com/user-attachments/assets/26e6cf73-1710-49b2-b429-2c26a15b65c5)


## Pathfinder Graph

![image](https://github.com/PauloWgDev/TwitterPathfinder/blob/main/Graphs/Pathfinder/guillermodb21_korn.png)

## Longest path on our Network

![image](https://github.com/PauloWgDev/TwitterPathfinder/blob/main/Graphs/Pathfinder/longest_path.png)
