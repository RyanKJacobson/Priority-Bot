# Priority-Bot

A discord bot that can post and edit priority lists in designated channels. Originally created for Qvex at Queen's University.

# Commands

* /addpriority \<item\> \<priority level\> \<status\> \<description (Optional)\>
  * Adds a new priority item to the list with a priority level, status of completion, and an optional description.
 
* /editpriority \<item\> \<priority level\ (Optional)> \<status (Optional\> \<description (Optional)\>
  * Edit a priority item, selected with the items name.
 
* /removepriority \<item\>
  * Removes a priority from the list.
 
* /getchannels
  * See which channels have a priority list.
 
* /setchannel \<channel\>
  * Sets a channel to have a priority list.
  * Caller requires server admin.

* /forgetchannel \<channel\>
  * Stops the bot from editing the channel.
  * Caller requires server admin.
