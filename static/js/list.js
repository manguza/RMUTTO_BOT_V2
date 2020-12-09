function trueDelete(id){
    var conf = confirm("คุณต้องการลบข้อมูล "+ id +" หรือไม่ ?");
    if(conf == true){
        alert('ลบข้อมูล '+ id +' สำเร็จ');
        return true;
    }else{
        alert("ยกเลิกการลบข้อมูล");
        return false;
    }
    
}

// Get the modal
var modal = document.getElementById('id');

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

$(document).ready(function(){
    $('.mydatatable').DataTable({
        // order: [[3, 'desc']],
        pagingType: 'full_numbers',
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]],
        // responsive: true,
        "scrollY" : 400,
        "scrollX" : true,
        "scrollCollapse": true,
        "ordering": false
        
        });
    });