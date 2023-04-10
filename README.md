# scrappe_airbnb_reservations
This is a Python script that scrapes data from the Airbnb website, specifically the reservation page for the host. The script requires the Selenium, BeautifulSoup, and Google API libraries.

The script logs into Airbnb using the provided credentials, navigates to the reservation page, and extracts guest names, room titles, check-in dates, and check-out dates. The extracted data is stored in separate lists.

The script also includes code for handling SMS verification if needed during the login process.

Finally, the script uses the extracted data to create events in a Google Calendar using the Google Calendar API. The Google API credentials are stored in a separate JSON file, and the events are created using a batch request to minimize the number of API calls.

To run the script, the user must have Google Chrome installed and a ChromeDriver executable file placed in the same directory as the script. The user must also update the email and password variables with their own Airbnb login credentials, and the GOOGLE_CREDENTIALS_FILE variable with the path to their own Google API credentials file.
