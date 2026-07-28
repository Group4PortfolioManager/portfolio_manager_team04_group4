function StatTile({ label, value }) {
  return (
    <div className="stat-tile">
      <h3>{label}</h3>
      <p>{value}</p>
    </div>
  );
}

export default StatTile;
