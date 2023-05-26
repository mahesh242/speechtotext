jQuery(document).ready(function () {
  var $ = jQuery;
  var myRecorder = {
    objects: {
      context: null,
      stream: null,
      recorder: null
    },
    init: function () {
      if (null === myRecorder.objects.context) {
        myRecorder.objects.context = new (
          window.AudioContext || window.webkitAudioContext
        );
      }
    },

    start: function () {
      var options = { audio: true, video: false };
      navigator.mediaDevices.getUserMedia(options).then(function (stream) {
        myRecorder.objects.stream = stream;
        myRecorder.objects.recorder = new Recorder(
          myRecorder.objects.context.createMediaStreamSource(stream),{ numChannels: 1 }
        );
        myRecorder.objects.recorder.record();
      }).catch(function (err) { });
    },

    stop: function (listObject) {
      if (null !== myRecorder.objects.stream) {
        myRecorder.objects.stream.getAudioTracks()[0].stop();
      }
      if (null !== myRecorder.objects.recorder) {
        myRecorder.objects.recorder.stop();

        // Validate object
        if (null !== listObject && 'object' === typeof listObject && listObject.length > 0) {
          // Export the WAV file
          myRecorder.objects.recorder.exportWAV(function (blob) {
            sendAudioToPython(blob)
            var url = (window.URL || window.webkitURL)
              .createObjectURL(blob);

            // Prepare the playback
            var audioObject = $('<audio controls></audio>').attr('src', url);
              
              // Prepare the download link
              var downloadObject = $('<a>&#9660;</a>').attr('href', url)
              .attr('download', new Date().toUTCString() + '.wav');

            // Wrap everything in a row
            var holderObject = $('<div class="row"></div>').append(audioObject).append(downloadObject);

            // Append to the list
            // listObject.append(holderObject);
          });
        }
      }
    }
  };

  // Prepare the recordings list
  var listObject = $('[data-role="recordings"]');

  // Prepare the record button
  $('[data-role="controls"] > button').click(function () {
    // Initialize the recorder
    myRecorder.init();

    // Get the button state 
    var buttonState = !!$(this).attr('data-recording');

    // Toggle
    if (!buttonState) {
      $(this).attr('data-recording', 'true');
      myRecorder.start();
    } else {
      $(this).attr('data-recording', '');
      myRecorder.stop(listObject);
    }
  });

  // Send the recorded audio to the Python function
  function sendAudioToPython(blob) {
    console.log("blob",blob)
    var formData = new FormData();
    formData.append('audio', blob, 'recording.wav');
    var url = $("#url_id").attr("data-url");
    console.log(formData.get('audio'));
    $.ajax({
      url: url, // Replace with the appropriate endpoint URL
      type: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken') // Modify to get the CSRF token from the cookie
      },
      data: formData,
      processData: false,
      contentType: false,
      success: function(response) {
        console.log(response,'Audio sent successfully.');
        var responseElement = document.getElementById('convert_text_id');
        responseElement.textContent = response;
        // Handle the response from the Python function if needed
      },
      error: function(xhr, status, error) {
        console.error('Error sending audio:', error);
      }
    });
  }
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  

});

