$(document).ready(function () {
  $('.search-input').on('input', function () {
    // Get values from each search bar
    var searchNumber = $('#flight_number').val();
    var searchAirline = $('#flight_airline').val();
    var searchStatus = $('#flight_status').val();
    var searchLimit = $('#flight_limit').val();

    // Perform AJAX request with multiple parameters
    $.ajax({
      type: 'POST',
      url: '/profile/search_flights',
      data: {
        flight_number: searchNumber,
        flight_airline: searchAirline,
        flight_status: searchStatus,
        flight_limit: searchLimit
      },
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
            '<p>Destination: ' + data[i].destination + ', Departure: ' + data[i].departure + '</p>'
          );

          // Append the container to the searchResults div
          searchResults.append(resultContainer);
        }
      },
      error: function (xhr, status, error) {
        console.error('Error:', error);
      }
    });
  });
});