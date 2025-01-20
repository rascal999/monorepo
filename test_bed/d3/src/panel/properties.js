export function displayNodeProperties(node) {
  const detailsDiv = document.getElementById('node-details');
  detailsDiv.innerHTML = `
    <div class="detail-item">
      <strong>ID:</strong> ${node.id}
    </div>
    <div class="detail-item">
      <strong>Name:</strong> ${node.name}
    </div>
    <div class="detail-item">
      <strong>Position:</strong> (${Math.round(node.x)}, ${Math.round(node.y)})
    </div>
  `;
}
