(function(){
  function attachAutocomplete(input, box){
    if(!input || !box) return;
    const suggestUrl = input.getAttribute('data-suggest-url') || '/catalog/suggest/';
    let abortController = null;
    let lastQuery = '';

    function clearSuggestions(){
      box.innerHTML='';
      box.style.display='none';
    }
    function renderSuggestions(items){
      if(!items || !items.length){clearSuggestions();return;}
      box.innerHTML = items.map((it, idx)=>{
        const id = 'sg-'+idx;
        return `<div role="option" class="sg-item" data-slug="${it.slug}" id="${id}" style="padding:8px 10px;cursor:pointer;border-bottom:1px solid #f4f4f4">`+
               `<div style="font-weight:600">${it.title}</div>`+
               `<div class="muted small">${it.authors||''}</div>`+
               `</div>`;
      }).join('');
      box.style.display='block';
      Array.from(box.querySelectorAll('.sg-item')).forEach(el=>{
        el.addEventListener('click', ()=>{
          window.location.href = '/catalog/book/'+el.getAttribute('data-slug')+'/';
        });
      });
    }

    let debounceTimer=null;
    input.addEventListener('input', function(){
      const q = input.value.trim();
      if(q === lastQuery){ return; }
      lastQuery = q;
      if(!q){ clearSuggestions(); return; }
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(()=>{
        if(abortController){ abortController.abort(); }
        abortController = new AbortController();
        fetch(suggestUrl+`?q=${encodeURIComponent(q)}`, {signal: abortController.signal})
          .then(r=>r.ok?r.json():{suggestions:[]})
          .then(data=>renderSuggestions(data.suggestions||[]))
          .catch(()=>{});
      }, 150);
    });

    document.addEventListener('click', (e)=>{
      if(!box.contains(e.target) && e.target !== input){ clearSuggestions(); }
    });
  }

  // Header search (existing IDs)
  const headerInput = document.getElementById('tbss-search');
  const headerBox = document.getElementById('tbss-suggest');
  if(headerInput && headerBox){
    attachAutocomplete(headerInput, headerBox);
  }

  // Any additional search inputs that declare a suggest target
  document.querySelectorAll('input[data-suggest-url][data-suggest-target]').forEach(inp=>{
    const sel = inp.getAttribute('data-suggest-target');
    const box = document.querySelector(sel);
    if(box) attachAutocomplete(inp, box);
  });
})();
