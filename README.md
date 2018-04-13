# music_database

Columbia University COMS W4111, Spring 2018

Project 1 Part 3

rmb2208 and sjm2221

PostgreSQL Account: rmb2208
URL: http://35.196.208.102:8111/

Implemented:
*User can add and see list of friends
*User can save music/albums to library
*User can create and edit playlists
*Search database for artists, albums, songs, genres
*Assign ratings to albums and songs
*User can suggest songs that appear on other user's profile

Not Implemented:
*Can't search users (but can add), playlists, ratings–time constraint
*No collaborative playlists–difficulty with our schema
*Cannot suggest artists or albums–time constraint

Intersting Web Pages:
View Friends: users are able to go to profiles of friends who have added them and see public aspects of their profile.
  The user's userid is remembered and then we query multiple tables in the database using this information.
Search by Genre: users can enter a genre and all albums and songs associated with that genre will appear. The user can then add songs to their library and/or playlists and also view the songs in the albums.
  The user enters the genre and we query the database for entities associated with that genre. Users can then input song information and/or album information and add to library and/or playlists.
