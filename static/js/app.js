document.addEventListener('DOMContentLoaded', () => {
    if (location.pathname === '/products') {
        fetch('/api/products')
            .then(r => r.json())
            .then(data => {
                const t = document.getElementById('productsTable');
                data.forEach(p => {
                    const r = document.createElement('tr');
                    r.innerHTML = `
                        <td>${p.name}</td>
                        <td>${p.sku}</td>
                        <td>${p.category}</td>
                        <td>${p.current_stock}</td>
                        <td><button class="btn-primary view" data-id="${p.id}">View</button></td>
                    `;
                    t.append(r);
                });
            })
            .then(() => document.querySelectorAll('.view').forEach(b => b.onclick = () => location = '/product/' + b.dataset.id));
        document.getElementById('productForm').onsubmit = e => {
            e.preventDefault();
            fetch('/api/products', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: document.getElementById('name').value,
                    sku: document.getElementById('sku').value,
                    category: document.getElementById('category').value,
                    initial_stock: +document.getElementById('initial_stock').value
                })
            }).then(() => location.reload());
        };
    }
    if (location.pathname.startsWith('/product/')) {
        fetch(`/api/products/${productId}/transactions`)
            .then(r => r.json())
            .then(data => {
                const t = document.getElementById('transactionsTable');
                data.forEach(x => {
                    const r = document.createElement('tr');
                    r.innerHTML = `
                        <td>${x.type}</td>
                        <td>${x.quantity}</td>
                        <td>${new Date(x.timestamp).toLocaleString()}</td>
                        <td><button class="btn-primary print" data-id="${x.id}" data-type="${x.type}" data-qty="${x.quantity}" data-ts="${x.timestamp}">Print</button></td>
                    `;
                    t.append(r);
                });
            })
            .then(() => document.querySelectorAll('.print').forEach(btn => btn.onclick = () => {
                const id = btn.dataset.id;
                const type = btn.dataset.type;
                const qty = btn.dataset.qty;
                const ts = new Date(btn.dataset.ts).toLocaleString();
                const w = window.open('', '_blank');
                w.document.write(`<h2>Transaction ${id}</h2><p>Type: ${type}</p><p>Quantity: ${qty}</p><p>Timestamp: ${ts}</p>`);
                w.print();
                w.close();
            }));
        document.getElementById('transactionForm').onsubmit = e => {
            e.preventDefault();
            fetch('/api/transactions', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    product_id: productId,
                    type: document.getElementById('type').value,
                    quantity: +document.getElementById('quantity').value
                })
            }).then(() => location.reload());
        };
    }
});