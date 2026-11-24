let erp = null;
const $ = (id) => document.getElementById(id);
function parseResult(raw) {
  const result = JSON.parse(raw);
  if (!result.success) throw new Error(result.error || "Operation failed");
  return result.data;
}
function callBridge(method, ...args) {
  return new Promise((resolve, reject) => {
    if (!erp) return reject(new Error("Desktop bridge is not ready. Restart the application."));
    erp[method](...args, raw => {
      try { resolve(parseResult(raw)); } catch (e) { reject(e); }
    });
  });
}
function toast(message) {
  const el = $("toast"); el.textContent = message; el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 3000);
}
function showPage(page) {
  document.querySelectorAll(".page").forEach(p => p.classList.toggle("active", p.id === page));
  document.querySelectorAll(".nav").forEach(b => b.classList.toggle("active", b.dataset.page === page));
  const titles = {dashboard:"Command Centre",company:"Company Master",products:"Product Master",movement:"Stock In / Out",reports:"Stock Report"};
  $("page-title").textContent = titles[page] || "Inventory ERP";
  if (page === "reports" || page === "dashboard" || page === "products" || page === "movement") refreshAll();
}
document.querySelectorAll(".nav").forEach(b => b.addEventListener("click", () => showPage(b.dataset.page)));
function money(value) { return "₹" + Number(value || 0).toLocaleString("en-IN",{minimumFractionDigits:2,maximumFractionDigits:2}); }
function esc(value) { return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }

async function loadCompany() {
  const c = await callBridge("get_company");
  $("company-name").value = c.name || "";
  $("company-address").value = c.address || "";
  $("company-gstin").value = c.gstin || "";
  $("company-msme").value = c.msme || "";
}
async function loadProducts() {
  const products = await callBridge("get_products");
  $("products-table").innerHTML = products.map(p => `<tr>
    <td>${esc(p.sku)}</td><td>${esc(p.name)}</td><td>${esc(p.category)}</td>
    <td>${esc(p.unit)}</td><td>${money(p.purchase_price)}</td>
    <td><b>${Number(p.balance).toLocaleString("en-IN")}</b></td>
    <td>${Number(p.reorder_level).toLocaleString("en-IN")}</td></tr>`).join("") || `<tr><td colspan="7" class="empty">No products added yet.</td></tr>`;
  $("movement-product").innerHTML = `<option value="">Choose a product</option>` + products.map(p =>
    `<option value="${p.id}">${esc(p.sku)} — ${esc(p.name)} (Balance: ${p.balance} ${esc(p.unit)})</option>`).join("");
  return products;
}
async function loadReport() {
  const report = await callBridge("get_stock_report");
  $("stat-products").textContent = report.product_count;
  $("stat-units").textContent = Number(report.total_units).toLocaleString("en-IN");
  $("stat-value").textContent = money(report.stock_value);
  $("stat-low").textContent = report.low_stock_count;
  $("low-stock-list").innerHTML = report.low_stock.length ? report.low_stock.map(p =>
    `<div class="alert-row">${esc(p.sku)} — ${esc(p.name)}: ${p.balance} ${esc(p.unit)} remaining</div>`).join("") : "No low-stock products to display.";
  $("report-table").innerHTML = report.products.map(p => `<tr>
    <td>${esc(p.sku)}</td><td>${esc(p.name)}</td><td>${esc(p.category)}</td>
    <td><b>${p.balance}</b></td><td>${esc(p.unit)}</td><td>${p.reorder_level}</td>
    <td class="${Number(p.balance)<=Number(p.reorder_level)?"status-low":"status-ok"}">${Number(p.balance)<=Number(p.reorder_level)?"LOW STOCK":"IN STOCK"}</td></tr>`).join("") || `<tr><td colspan="7">No products found.</td></tr>`;
  const rows = report.movements.map(m => `<tr><td>${esc(m.created_at)}</td><td>${esc(m.sku)}</td><td>${esc(m.name)}</td>
    <td class="${m.movement_type==="IN"?"tag-in":"tag-out"}">${m.movement_type}</td><td>${m.quantity} ${esc(m.unit)}</td><td>${esc(m.note)}</td></tr>`).join("") || `<tr><td colspan="6">No stock movements recorded.</td></tr>`;
  $("history-table").innerHTML = rows;
  $("recent-movements").innerHTML = rows;
}
async function refreshAll() {
  try { await loadProducts(); await loadReport(); }
  catch(e) { toast(e.message); }
}
$("company-form").addEventListener("submit", async e => {
  e.preventDefault();
  try {
    await callBridge("save_company",$("company-name").value,$("company-address").value,$("company-gstin").value,$("company-msme").value);
    $("company-message").textContent = "Saved successfully.";
    toast("Company details saved.");
  } catch(err) { toast(err.message); }
});
$("product-form").addEventListener("submit", async e => {
  e.preventDefault();
  try {
    await callBridge("add_product",$("sku").value,$("product-name").value,$("category").value,$("unit").value,$("price").value,$("reorder").value);
    e.target.reset(); $("price").value="0"; $("reorder").value="0";
    $("product-message").textContent="Product added successfully.";
    await refreshAll(); toast("Product added.");
  } catch(err) { toast(err.message); }
});
$("movement-form").addEventListener("submit", async e => {
  e.preventDefault();
  try {
    await callBridge("stock_movement",$("movement-product").value,$("movement-type").value,$("movement-qty").value,$("movement-note").value);
    e.target.reset(); await refreshAll(); toast("Stock movement saved.");
  } catch(err) { toast(err.message); }
});
function initializeBridge() {
  new QWebChannel(qt.webChannelTransport, async channel => {
    erp = channel.objects.erp;
    $("today").textContent = new Date().toLocaleDateString("en-IN",{day:"2-digit",month:"short",year:"numeric"});
    try { await loadCompany(); await refreshAll(); }
    catch(e) { toast(e.message); }
  });
}
if (typeof qt !== "undefined" && typeof QWebChannel !== "undefined") initializeBridge();
else document.addEventListener("DOMContentLoaded", () => {
  if (typeof qt !== "undefined" && typeof QWebChannel !== "undefined") initializeBridge();
});
