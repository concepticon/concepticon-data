function getGlossesBySimilarity(gloss) {
  var glosses, table, i, j, new_gloss, splitted, out;
  var alphabet = 'abcdefghijklmnopqrstuvwxyz';
  
  function add_or_not(item, dict, sim) {
    if (!(item in dict)) {
      dict[item] = sim;
    }
  }
  
  function delchar(word) {
    if (!word) {
      return [];
    }
    out = [];
    for (i=0; i<=word.length; i++) {
      new_gloss = word.slice(0, i) + word.slice(i+1, word.length);
      out.push([new_gloss, 1]);
      out.push([new_gloss.toUpperCase(), 2]);
      out.push([new_gloss.toLowerCase(), 2]);
    }
    return out;
  }
  
  function subchar(word, alphabet) {
    if (!word) {
      return [];
    }
    out = [];
    for (i=0; i<=word.length; i++) {
      for (j=0; j<alphabet.length; j++) {
	new_gloss = word.slice(0, i) +
	  alphabet[j] +
	  word.slice(i+1, word.length);
	out.push([new_gloss, 3]);
	out.push([new_gloss.toUpperCase(), 4]);
	out.push([new_gloss.toLowerCase(), 4]);
      }
    }
    return out;
  }

  function addchar(word, alphabet) {
    var word_array, out, new_gloss;
    if (!word) {
      return [];
    }
    out = [];
    for (i=0; i<=word.length; i++) {
      for (j=0; j<alphabet.length; j++) {
	word_array = word.split('');
	word_array.splice(i, 0, alphabet[j]);
	new_gloss = word_array.join('')
	out.push([new_gloss, 3]);
	out.push([new_gloss.toUpperCase(), 4]);
	out.push([new_gloss.toLowerCase(), 4]);
      }
      console.log(new_gloss);
    }
    return out;
  }

  glosses = {};
  glosses[gloss] = 0

  /* start deleting one sound */
  out = delchar(gloss);
  for (i=0; i<out.length; i++) {
    add_or_not(out[i][0], glosses, out[i][1]);
  }
  out = subchar(gloss, alphabet);
  for (i=0; i<out.length; i++) {
    add_or_not(out[i][0], glosses, out[i][1]);
  }
  out = subchar(gloss, alphabet.toUpperCase());
  for (i=0; i<out.length; i++) {
    add_or_not(out[i][0], glosses, out[i][1]);
  }
  out = addchar(gloss, alphabet);
  for (i=0; i<out.length; i++) {
    add_or_not(out[i][0], glosses, out[i][1]);
  }

  splitted = gloss.split(' ');
  if (splitted.length > 1) {
    for (i=0; i<splitted.length; i++) {
      out = delchar(splitted[i]);
      for (j=0; j<out.length; j++) {
	add_or_not(out[j][0], glosses, 4+out[j][1]);
      }
      out = subchar(splitted[i], alphabet);
      for (j=0; j<out.length; j++) {
	add_or_not(out[j][0], glosses, 6+out[j][1]);
      }
    }
  }

  glosses = Object.entries(glosses);
  glosses.sort(function (x, y) {
    if (x[1] > y[1]) {
      return 1;
    }
    else if (x[1] < y[1]) {
      return -1;
    }
    else {
      return x[0].localeCompare(y[0]);
    }
  });
  return glosses;
}


function filterConcepts(value, language) {
  if (!value.replace(/\s/g, '')) {
    document.getElementById('output').innerHTML = '';
  }

  var text, cgl, cid, i, row, table, results, visited;
  if (typeof language=='undefined') {
    language = Concepticon.language;
  }
  
  glosses = getGlossesBySimilarity(value);
  visited = [];
  table = [];
  for (i=0; i<glosses.length; i++) {
    results = Concepticon[glosses[i][0]+'---'+language];
    if (typeof results !== 'undefined') {
      for (j=0; j<results.length; j++) {
	if (visited.indexOf(results[j][0]) === -1) {
	  visited.push(results[j][0]);
	  table.push([
	      glosses[i][0],
	      results[j][0],
	      results[j][1],
	      results[j][2],
	      glosses[i][1]]);
	}
      }
    }
  }
  if (table.length == 0) {
    document.getElementById('output').innerHTML = '';
    return;
  }
  text = '<table><tr>' +
    '<th>MATCH</th>' +
    '<th>ID</th>' +
    '<th>GLOSS</th>' +
    '<th>DEFINITION</th>' +
    '<th>SIMILARITY</th>'+
    '</tr>';
  
  table.sort(function (x, y){
    if (x[4] > y[4]) {return 1;}
    else if (x[4] < y[4]){return -1;}
    else {return 0;}
  });
 
  for (i=0; row=table[i]; i++){
    text += '<tr>' +
      '<td>' + row[0] + '</td>' +
      '<td><a target="_blank" href="http://concepticon.clld.org/parameters/'+row[1]+'">' + row[1] + '</td>' +
      '<td>' + row[2] + '</td>' +
      '<td>' + row[3] + '</td>' +
      '<td>' + row[4] + '</td>' +
      '</tr>';
  }
  document.getElementById('output').innerHTML = text;
  return;
};
