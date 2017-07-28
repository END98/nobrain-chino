var url = "../cgi-bin/chatbot.py";

  function json(){
      var txt = $('#txt').val();
      $.get(url, { "m": "say", "txt": txt },
        function(res){
            $("#result").html("チノちゃん「 " + res + "」")
        });
  }
  
  function esc(s){
      return s.replace('&','&amp;').replace('<','&lt;')
      .replace('>','&gt;');
  }










  /*
  //f jsonp and f callback is from python to js
  function callback(json) {
    console.log("good night");
    $("#result").html("答えは "+json.txt);
  }
  function jsonp(){
      //var txt = $('#txt').val();
      //console.log(txt)
      var s = document.createElement('script');
      s.src = '/app/cgi-bin/jsonp.py';
      document.body.appendChild(s);
      return false;
  }
*/