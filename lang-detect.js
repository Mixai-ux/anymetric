(function () {
  if (localStorage.getItem('am_lang_chosen')) return;
  var c = (document.cookie.match(/(?:^|;\s*)am_country=([^;]+)/) || [])[1] || '';
  var deC = ['de', 'at', 'ch'], ruC = ['ru', 'by', 'kz'];
  var n = (navigator.language || '').slice(0, 2).toLowerCase();
  var loc;
  if (deC.indexOf(c.toLowerCase()) !== -1) loc = 'de';
  else if (ruC.indexOf(c.toLowerCase()) !== -1) loc = 'ru';
  else if (deC.indexOf(n) !== -1) loc = 'de';
  else if (n === 'ru') loc = 'ru';
  else loc = 'en';
  localStorage.setItem('am_lang_chosen', 'auto');
  if (loc !== 'en') window.location.replace('/' + loc + '/');
}());
