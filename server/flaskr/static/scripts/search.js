$(document).ready(function () {
   $('#flightSearch').on('input', function () {
     var searchValue = $(this).val();

     // Check if the search bar is empty
     if (searchValue.trim() === '') {
       // Clear existing search results and flight number display
       $('#searchResults').empty();
       $('#flightNumberDisplay').text('');
       return;
     }

     $.ajax({
       type: 'POST',
       url: '/profile/search_flights',
       contentType: 'application/json;charset=UTF-8',  // Set content type to JSON
       data: JSON.stringify({ search: searchValue }),  // Send data as JSON
       success: function (data) {
         // Display the flight number underneath the search bar
         var flightNumberDisplay = $('#flightNumberDisplay');
         
         // Check if data is not empty and contains a flight number
         if (data.length > 0 && data[0].flight_number) {
           flightNumberDisplay.text('Flight Number: ' + data[0].flight_number);
         } else {
           flightNumberDisplay.text('No matching flight found');
         }

         // You can also display other flight information in the searchResults div
         var searchResults = $('#searchResults');
         searchResults.empty();

         for (var i = 0; i < data.length; i++) {
           // Create a container for each search result
           var resultContainer = $('<div class="search-result-container"></div>');

           // Append result details to the container
           resultContainer.append(
             "<p><br>Departure: " + data[i].departure + "<br>Destination: " + data[i].destination + "</p>"
           );

           // Append the container to the searchResults div
           searchResults.append(resultContainer);
         }
       }
     });
   });
 });