$(document).ready(function () {
  $('.search-input').on('input', function () {
    let searchNumber = $('#flight_number').val();
    let searchAirline = $('#flight_airline').val();
    let searchStatus = $('#flight_status').val();
    let searchLimit = $('#flight_limit').val();

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
        let flightNumberDisplay = $('#flightNumberDisplay');

        if (data.length > 0 && data[0].flight_number) {
          flightNumberDisplay.text('Flight Number: ' + data[0].flight_number);
        } else {
          flightNumberDisplay.text('No matching flight found');
        }

        let searchResults = $('#searchResults');
        searchResults.empty();

        for (var i = 0; i < data.length; i++) {
          let resultContainer = $('<div class="search-result-container"></div>');

          resultContainer.append(
            '<p>Destination: ' + data[i].destination + ', Departure: ' + data[i].departure + '</p>'
          );

          searchResults.append(resultContainer);
        }
      },
      error: function (xhr, status, error) {
        console.error('Error:', error);
      }
    });
  });
});