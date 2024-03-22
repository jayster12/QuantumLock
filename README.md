# QuantumLock

Password Manager Project For Class

# Progress

- [x] Login functionality

- [x] Dashboard functionality

* ~~Need to modify the current dashboard to display user's saved passwords~~
* ~~Need to modify background of dashboard to match overall website theme~~


- [x] Registration functionality


- [x] Password entry creation functionality


- [] Profile functionality


- [x] Password reset functionality


- [] Settings functionality


- [] Password sharing functionality


- [x] Password generator


- [] Password strength checker


- [] Secure note functionality


- [] Ability to edit current password entries


- [x] Ability to delete password entries

    - NOTE: Weird problem with this in previous versions due to the HTML. When you would click delete password for the first password entry, it would send empty POST request to `/add-password` endpoint & add a blank password. Fixed by moving the `div` around for the `/add-password` element 


- [x] When adding password entries, check to see if the entry is empty before allowing it to be submitted. It must have at least a username and password inputted. Otherwise, don't accept the POST request