$(function() {
  $('#btnSearch').click(function() {
    $.ajax({
      url: '/',
      data: $('form').serialize(),
      type: 'POST',
      success: function(response) {
        var jsonData = JSON.parse(response);
        // Show Results Section
        var resultsDiv = document.getElementById('results');
        if (resultsDiv.style.display === 'none') {
            resultsDiv.style.display = 'block';
        }
        var errorsDiv = document.getElementById('errors');
        if (errorsDiv.style.display === 'block') {
          errorsDiv.style.display = 'none';
        }
        // LINKS section
        document.getElementById('linksSection').innerHTML = "";
        $('#linksSection').append(jsonDataToList(jsonData['links']));
        // ADDRESS section
        document.getElementById('addressSection').innerHTML = "";
        $('#addressSection').append(jsonDataToList(jsonData['address']));
        // ZESTIMATE section
        document.getElementById('zestimateSection').innerHTML = "";
        $('#zestimateSection').append(jsonDataToList(jsonData['zestimate']));
        // LOCALREALESTATE section
        document.getElementById('localRealEstateSection').innerHTML = "";
        $('#localRealEstateSection').append(jsonDataToList(jsonData['localRealEstate']))
      },
      error: function(error) {
        var resultsDiv = document.getElementById('results');
        if (resultsDiv.style.display === 'block') {
          resultsDiv.style.display = 'none';
        }
        var errorsDiv = document.getElementById('errors');
        if (errorsDiv.style.display === 'none') {
          errorsDiv.style.display = 'block';
        }
        document.getElementById('errorInfo').innerHTML = "";
        var errorString = "<p>" + error.responseText + "</p>";
        document.getElementById('errorInfo').innerHTML = errorString;
        console.log(error.responseText);
      }
    });
  });
});

function jsonDataToList(jsonData) {
  var ul = $('<ul>');
  $(jsonData).each(function(index, item) {
    if (item.includes("http")) {
      // link found...format as needed
      var htmlLink = createHtmlLink(item);
      var li = document.createElement('li');
      li.appendChild(htmlLink);
      ul.append(li);
    } else {
      ul.append(
        $(document.createElement('li')).text(item)
      );      
    }

  });
  return ul;
}

function createHtmlLink(linkString) {
  // format: display_text;link
  var splitString = linkString.split(";");

  var link = document.createElement('a');
  var linkText = document.createTextNode(splitString[0]);
  link.appendChild(linkText);
  link.title = splitString[0];
  link.href = splitString[1];
  link.target = "_blank";
  return link;
}
