(function($){
    var master_name = $('#top-nav').find('strong').text();
    master_name =  master_name.substring(4);
    add_balance();
　　function add_balance() {

      $(".addbalance").click(function () {
          //增加余额
            userid = $(this).attr('userid');
            var input_fee = prompt("请输入给用户【" + userid + "】添加的余额");
            var fee = parseFloat(input_fee);

            if((typeof fee =="number") && fee > 0 ){
                if(window.confirm('你确定要给'+userid+'增加余额'+fee+'元吗？')){
                    var desc = prompt("增加佣金说明(若不填默认为'延迟到账提醒')");
                    url = window.location.protocol + '//' + window.location.host + '/opebalance/';
                     $.ajax({
            　　　　　　　　type:"POST",
            　　　　　　　　url:url,
                          data:{'userid':userid,'fee':fee,'desc':desc, 'ope_user': master_name, 'type': 'add'},
            　　　　　　　　beforeSend:function(xhr){
            　　　　　　　　　　xhr.setRequestHeader("X-CSRFToken", $.getCookie("csrftoken"))
            　　　　　　　　},
            　　　　　　　　success:function(data){
                            alert(data.msg);
                            window.location.reload();

            　　　　　　　　},
            　　　　　　　　error:function(xhr){
                              alert("出现未知错误");
            　　　　　　　　　　window.location.reload();
            　　　　　　　　　　
            　　　　　　　　}
            　　　　　　});
                     return true;
                  }else{

                     return false;
                 }
            }
      });
      $(".subbalance").click(function () {
          //扣除余额
            userid = $(this).attr('userid');
            var input_fee = prompt("请输入给用户【" + userid + "】扣除的余额");
            var fee = parseFloat(input_fee);

            if((typeof fee =="number") && fee > 0 ){
                if(window.confirm('你确定要给'+userid+'扣除余额'+fee+'元吗？')){
                    var desc = prompt("扣除佣金说明");
                    url = window.location.protocol + '//' + window.location.host + '/opebalance/';
                     $.ajax({
            　　　　　　　　type:"POST",
            　　　　　　　　url:url,
                          data:{'userid':userid,'fee':fee,'desc':desc, 'ope_user': master_name, 'type': 'sub'},
            　　　　　　　　beforeSend:function(xhr){
            　　　　　　　　　　xhr.setRequestHeader("X-CSRFToken", $.getCookie("csrftoken"))
            　　　　　　　　},
            　　　　　　　　success:function(data){
                            alert(data.msg);
                            window.location.reload();

            　　　　　　　　},
            　　　　　　　　error:function(xhr){
                              alert("出现未知错误");
            　　　　　　　　　　window.location.reload();
            　　　　　　　　　　
            　　　　　　　　}
            　　　　　　});
                     return true;
                  }else{

                     return false;
                 }
            }
      });
   }
　　
})(jQuery);