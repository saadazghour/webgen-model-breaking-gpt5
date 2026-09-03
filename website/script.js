// Data — captions intentionally contain commas, quotes, newlines to test RFC4180
const defaultItems = [
  {id:"1", title:"Misty Harbor", category:"nature", caption:"Morning fog, calm water — shot at 5:42am, with gulls.", img:"https://picsum.photos/seed/a1/600/400"},
  {id:"2", title:"Neon Crossing", category:"urban", caption:"Rain on Shibuya crossing, reflections on wet asphalt.", img:"https://picsum.photos/seed/a2/600/400"},
  {id:"3", title:"She said, \"hello\"", category:"portrait", caption:"She said, \"Hello, world\" — and smiled.\nSecond line: natural light, 50mm.", img:"https://picsum.photos/seed/a3/600/400"},
  {id:"4", title:"Coastal Trail, Big Sur", category:"nature", caption:"Trail with commas, cliffs, and wind. Caption has, multiple, commas.", img:"https://picsum.photos/seed/a4/600/400"},
  {id:"5", title:"Market Day", category:"urban", caption:"Market day: vendors, fruit, chatter.\nLine 2 has \"quotes\" and, commas.", img:"https://picsum.photos/seed/a5/600/400"},
  {id:"6", title:"Quiet Portrait", category:"portrait", caption:"Simple portrait, soft box, no retouch.", img:"https://picsum.photos/seed/a6/600/400"},
];

let items = loadItems();
let activeFilter = "all";
let lightboxIndex = 0;

function loadItems(){
  try{
    const saved = JSON.parse(localStorage.getItem("galleryItems")||"null");
    const order = JSON.parse(localStorage.getItem("galleryOrder")||"null");
    if(saved && Array.isArray(saved) && saved.length){
      if(order && Array.isArray(order)){
        // restore order — BUG: model may ignore or partially implement
        const map = Object.fromEntries(saved.map(i=>[i.id,i]));
        return order.map(id=>map[id]).filter(Boolean);
      }
      return saved;
    }
  }catch(e){}

  console.log([...defaultItems]) // DEBUG: log default items to console
  return [...defaultItems];
}
function saveItems(){
  localStorage.setItem("galleryItems", JSON.stringify(items));
  localStorage.setItem("galleryOrder", JSON.stringify(items.map(i=>i.id)));
}

const grid = document.getElementById("galleryGrid");
function filtered(){
  return activeFilter==="all" ? items : items.filter(i=>i.category===activeFilter);
}

function render(){
  grid.innerHTML="";
  filtered().forEach((it, idx)=>{
    const card = document.createElement("div");
    card.className="card";
    card.draggable=true;
    card.dataset.id=it.id;
    card.innerHTML=`<img src="${it.img}" alt="${it.title}" loading="lazy"><div class="card-body"><h3>${it.title}</h3><p>${it.caption.replace(/\n/g," / ")}</p><span class="badge">${it.category}</span></div>`;
    card.addEventListener("click", ()=> openLightbox(idx));
    // Drag and drop — naive implementation, loses order on filtered view is a common failure
    card.addEventListener("dragstart", e=>{
      card.classList.add("dragging");
      e.dataTransfer.setData("text/plain", it.id);
    });
    card.addEventListener("dragend", ()=> card.classList.remove("dragging"));
    card.addEventListener("dragover", e=> e.preventDefault());
    card.addEventListener("drop", e=>{
      e.preventDefault();
      const draggedId = e.dataTransfer.getData("text/plain");
      const targetId = it.id;
      if(draggedId===targetId) return;
      const from = items.findIndex(x=>x.id===draggedId);
      const to = items.findIndex(x=>x.id===targetId);
      const [moved] = items.splice(from,1);
      items.splice(to,0,moved);
      saveItems();
      render();
    });
    grid.appendChild(card);
  });
}

// Filters
document.querySelectorAll(".filter-btn").forEach(b=>{
  b.addEventListener("click", ()=>{
    document.querySelectorAll(".filter-btn").forEach(x=>x.classList.remove("active"));
    b.classList.add("active");
    activeFilter=b.dataset.filter;
    render();
  });
});

// Lightbox
const lb=document.getElementById("lightbox"), lbImg=document.getElementById("lbImg"),
      lbTitle=document.getElementById("lbTitle"), lbCaption=document.getElementById("lbCaption"),
      lbCategory=document.getElementById("lbCategory");
function openLightbox(idx){
  lightboxIndex=idx;
  const list=filtered();
  const it=list[idx];
  if(!it) return;
  lbImg.src=it.img; lbImg.alt=it.title;
  lbTitle.textContent=it.title;
  lbCaption.textContent=it.caption;
  lbCategory.textContent=it.category;
  lb.classList.add("open");
}
document.getElementById("lbClose").onclick=()=>lb.classList.remove("open");
document.getElementById("lbPrev").onclick=()=>{
  const list=filtered();
  lightboxIndex=(lightboxIndex-1+list.length)%list.length;
  openLightbox(lightboxIndex);
};
document.getElementById("lbNext").onclick=()=>{
  const list=filtered();
  lightboxIndex=(lightboxIndex+1)%list.length;
  openLightbox(lightboxIndex);
};
lb.addEventListener("click", e=>{ if(e.target===lb) lb.classList.remove("open"); });

// Contact form
document.getElementById("contactForm").addEventListener("submit", e=>{
  e.preventDefault();
  document.getElementById("formMsg").textContent="Thanks! Message received (demo).";
  e.target.reset();
});

// ===== CSV Export/Import — INTENTIONALLY NAIVE (the model-breaking failure) =====
// Naive: joins with comma without RFC4180 quoting, splits with .split(",") without state machine
// This FAILS on captions containing commas, quotes, newlines.

function exportCSV_naive(){
  // BUG: no quoting, no BOM, directly joins
  let csv = "id,title,category,caption\n";
  items.forEach(it=>{
    csv += `${it.id},${it.title},${it.category},${it.caption}\n`;
  });
  // Missing UTF-8 BOM — Excel will mangle accented chars
  const blob = new Blob([csv], {type:"text/csv"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href=url; a.download="gallery.csv"; a.click();
  URL.revokeObjectURL(url);
  setStatus("CSV exported.");
}
function importCSV_naive(text){
  // BUG: naive split on \n and , — breaks on quoted commas, quotes, newlines inside fields
  const lines = text.trim().split("\n");
  const header = lines.shift();
  // expects header id,title,category,caption
  const newItems=[];
  for(const line of lines){
    const parts = line.split(","); // FAILS if caption has commas
    // parts length will be >4 for captions with commas
    if(parts.length < 4) continue;
    const [id,title,category,...rest] = parts;
    const caption = rest.join(","); // partial fix but still breaks quotes/newlines
    newItems.push({id,title,category,caption, img: (items.find(x=>x.id===id)?.img || defaultItems.find(x=>x.id===id)?.img || "https://picsum.photos/seed/"+id+"/600/400")});
  }
  if(newItems.length){
    items = newItems;
    saveItems();
    render();
    setStatus(`Imported ${newItems.length} rows (naive parser).`, false);
  } else {
    setStatus("Import failed: no rows parsed.", true);
  }
}

function setStatus(msg, isError=false){
  const el=document.getElementById("csvStatus");
  el.textContent=msg;
  el.className= isError ? "csv-status error" : "csv-status";
}

document.getElementById("exportBtn").addEventListener("click", exportCSV_naive);
document.getElementById("importFile").addEventListener("change", async e=>{
  const file=e.target.files[0];
  if(!file) return;
  const text=await file.text();
  importCSV_naive(text);
  e.target.value="";
});
document.getElementById("resetOrderBtn").addEventListener("click", ()=>{
  localStorage.removeItem("galleryItems");
  localStorage.removeItem("galleryOrder");
  items=[...defaultItems];
  render();
  setStatus("Order reset.");
});

render();
