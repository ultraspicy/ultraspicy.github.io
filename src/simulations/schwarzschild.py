"""
Flamm's paraboloid: the embedding diagram of the Schwarzschild spatial geometry.

Take the Schwarzschild metric at constant t and theta = pi/2:
    dl^2 = (1 - rs/r)^-1 dr^2 + r^2 dphi^2
Embed it as a surface z(r) in flat 3D space, dl^2 = dz^2 + dr^2 + r^2 dphi^2,
which gives  z(r) = 2 sqrt(rs (r - rs)).

Writes a self-contained HTML file into public/simulations/ for embedding
in an Astro page with an <iframe>, and a PNG fallback if kaleido is installed.

Run from the repo root:
    .venv/bin/python src/simulations/schwarzschild.py
"""
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

RS = 1.0            # Schwarzschild radius, sets the length unit
R_MAX = 10.0        # outer edge of the plotted sheet
N_R, N_PHI = 200, 200

OUT_DIR = Path(__file__).resolve().parents[2] / "public" / "simulations"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---- surface ---------------------------------------------------------------
r = np.linspace(RS, R_MAX, N_R)
phi = np.linspace(0, 2 * np.pi, N_PHI)
R, PHI = np.meshgrid(r, phi)
Z = -2 * np.sqrt(RS * (R - RS))          # negative so the throat points down
X, Y = R * np.cos(PHI), R * np.sin(PHI)

surface = go.Surface(
    x=X, y=Y, z=Z,
    surfacecolor=R,                      # color by radial coordinate
    colorscale="Viridis",
    showscale=False,
    opacity=0.95,
    hovertemplate="r = %{customdata:.2f} r_s<extra></extra>",
    customdata=R,
    contours={"z": {"show": True, "width": 1, "color": "rgba(255,255,255,0.25)",
                    "start": Z.min(), "end": 0, "size": 0.5}},
)

# ---- a few circular orbits drawn on the sheet for scale --------------------
orbit_traces = []
for r_orbit, label in [(1.5 * RS, "photon sphere 1.5 r_s"),
                       (3.0 * RS, "ISCO 3 r_s"),
                       (6.0 * RS, "6 r_s")]:
    z_orbit = -2 * np.sqrt(RS * (r_orbit - RS))
    orbit_traces.append(go.Scatter3d(
        x=r_orbit * np.cos(phi), y=r_orbit * np.sin(phi),
        z=np.full_like(phi, z_orbit),
        mode="lines", name=label,
        line={"width": 4, "color": "white"},
        hoverinfo="name",
    ))

# ---- event horizon ring ----------------------------------------------------
horizon = go.Scatter3d(
    x=RS * np.cos(phi), y=RS * np.sin(phi), z=np.zeros_like(phi),
    mode="lines", name="event horizon r = r_s",
    line={"width": 6, "color": "black"},
    hoverinfo="name",
)

fig = go.Figure(data=[surface, horizon, *orbit_traces])
fig.update_layout(
    title={"text": "Schwarzschild geometry, equatorial slice (Flamm's paraboloid)",
           "x": 0.5, "font": {"size": 16}},
    scene={
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
        "zaxis": {"visible": False},
        "aspectmode": "data",
        "camera": {"eye": {"x": 1.4, "y": 1.4, "z": 0.7}},
        "bgcolor": "rgba(0,0,0,0)",
    },
    paper_bgcolor="rgba(0,0,0,0)",
    legend={"x": 0.01, "y": 0.99, "bgcolor": "rgba(255,255,255,0.6)"},
    margin={"l": 0, "r": 0, "t": 40, "b": 0},
)

# ---- outputs ---------------------------------------------------------------
html_path = OUT_DIR / "schwarzschild.html"
fig.write_html(
    html_path,
    include_plotlyjs="cdn",              # ~small file; use True to inline the lib
    full_html=True,
    config={"displayModeBar": False, "responsive": True},
)
print(f"wrote {html_path}")

try:
    png_path = OUT_DIR / "schwarzschild.png"
    fig.write_image(png_path, width=1200, height=900, scale=2)
    print(f"wrote {png_path}")
except Exception as exc:                 # kaleido not installed, fine
    print(f"skipped PNG export ({exc.__class__.__name__}); pip install kaleido to enable")
