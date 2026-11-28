"""procedural-illustration: data figures for the blog drawn in code, in its design system.

    import sys; sys.path.insert(0, '.claude/skills/procedural-illustration/scripts')
    from pi import *

Every name a spec needs is exported here. See ../SKILL.md.
"""
from .figure import Figure, Component, tr
from .canvas import Canvas, shape_path, GLYPHS
from .charts2d import Bars, Line, Scatter, Dumbbell, Slope, Donut, make_fmt, place, spread
from .infographic import Units, Waffle, Stats, Compare, Timeline
from .flow import Flow, Node, Edge
from .geo import Map
from .iso3d import Bars3D, Surface3D, Blocks3D
from .eng import SLD, catenary
from . import fmt, metrics, tokens

__all__ = ['Figure', 'Component', 'tr', 'Canvas', 'shape_path', 'GLYPHS', 'Bars', 'Line', 'Scatter',
           'Dumbbell', 'Slope', 'Donut', 'make_fmt', 'place', 'spread', 'Units', 'Waffle', 'Stats',
           'Compare', 'Timeline', 'Flow', 'Node', 'Edge', 'Map', 'Bars3D', 'Surface3D', 'Blocks3D', 'SLD', 'catenary',
           'fmt', 'metrics', 'tokens']
