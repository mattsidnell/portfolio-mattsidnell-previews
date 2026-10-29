const menu=document.querySelector('.mobile-toggle');
const nav=document.querySelector('#nav');
menu.addEventListener('click',()=>{const open=nav.classList.toggle('open');menu.setAttribute('aria-expanded',String(open));menu.innerHTML=open?'Close <span>×</span>':'Menu <span>☰</span>';});
nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{nav.classList.remove('open');menu.setAttribute('aria-expanded','false');menu.innerHTML='Menu <span>☰</span>';}));
const filters=[...document.querySelectorAll('[data-filter]')],projects=[...document.querySelectorAll('[data-type]')];
filters.forEach(b=>b.addEventListener('click',()=>{const selected=b.dataset.filter;filters.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));projects.forEach(p=>p.hidden=selected!=='all'&&!p.dataset.type.split(' ').includes(selected));}));
