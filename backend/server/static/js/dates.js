document.getElementById("start_date").addEventListener("click", getDate);
document.getElementById("end_date").addEventListener("click", getDate);

function getDate() {
  let today = new Date();
  let ymd, year, month, date;
  year = String(today.getFullYear());
  if (today.getMonth() + 1 < 10) {
    month = "0" + String(today.getMonth() + 1);
  } else {
    month = String(today.getMonth() + 1);
  }
  date = today.getDate();
  ymd = year + "-" + month + "-" + date;
  document.getElementById("start_date").setAttribute("max", ymd);
  document.getElementById("end_date").setAttribute("max", ymd);
}
