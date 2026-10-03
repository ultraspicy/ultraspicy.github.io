---
title: Mathematics of General Relativity (WIP)
description: understand General Relativity and its mathematical tools
pubDate: 1970-01-01
tags: [science]
draft: true
---

## 1. What is General Relativity
Special Relativity (1905) merged space and time into a single four-dimensional spacetime. General Relativity, published by Einstein in 1915, goes one step further: spacetime is not a fixed stage but a curved geometry, shaped by the energy and matter within it. In this picture gravity is not a pulling force. A freely falling object is simply following the straightest possible path through curved spacetime, called a geodesic, in the same way an object in empty space moves in a straight line at constant speed when nothing acts on it.

John Wheeler summarized the two halves of the theory in one sentence: spacetime tells matter how to move, and matter tells spacetime how to curve.

## 2. Spacetime, worldline and proper time

### 2.1 Spacetime
Similar with how we define a position in one-dimension vector via $x$, two-diemsion plain surface via $(x,y)$ and three-dimenison space via $(x,y,z)$, we label an event in spacetime as a four number $(x, y, z, t)$. This is merely a coordinate and doesn't have any physical meaning yet. For simplicity, we use $(\vec{x},t)$ in the following discussion.

### 2.2 Worldline
An object's entire history, where it was at every instant, traces out a curve in spacetime. This curve is its worldline. We build coordinate system to decribe the worldline, but its shape is indepedently of what coordinate we choose.

### 2.3 Lorentz transformation
After the definition of spacetime event $e = (\vec{x}, t)$ and worldline, we can develop our first important formula: the Lorentz transformation. It reveals the relation of two inertial coordinate $(\vec{x}, t)$ and $(\vec{x^{\prime}}, t^{\prime})$. We assume
- Relativity. the law of physics are idential in all inertial system. In particular, $S$ sees $S^{\prime}$ move at +v, so S' must see S move at -v, and the inverse transformation must have the same form with v replaced by -v.
- Light speed. A light signal has speed c in every inertial frame.

#### 2.3.0 the setup
Two inertial frames $S$ and $S^{\prime}$. $S^{\prime}$ moves along the x axis of S with velocity v. The origins coincide at $t = t^{\prime} = 0$. An event has coordinates $(t, x)$ in S and $(t', x')$ in S'. The goal is to find the functions
$$
x^{\prime} = f(x, t)
\\
t^{\prime} = g(x, t)
$$

#### 2.3.1 transormation is linear
We want to express $(\vec{x^{\prime}}, t^{\prime})$ in terms of $(\vec{x}, t)$. Suppose
$$
\begin{aligned}
x^{\prime} = f(x, t)
\end{aligned} \tag{1}
$$
Suppose two pairs of events $(e_1, e_2)$ and $(e_3, e_4)$ has the same separation $(\delta{x}, \delta{t})$ in $S$,
$$
\begin{aligned}
(\delta{x}, \delta{t}) = e_2 - e_1 = e_4 - e_3
\end{aligned} \tag{2}
$$
then described by a different coordinate, $(e^{\prime}_1, e^{\prime}_2)$ and $(e^{\prime}_3, e^{\prime}_4)$ will still have the same separation $(\delta{x^{\prime}}, \delta{t^{\prime}})$ in $S^{\prime}$,
$$
\begin{aligned}
(\delta{x^{\prime}}, \delta{t^{\prime}}) = e^{\prime}_2 - e^{\prime}_1 = e^{\prime}_4 - e^{\prime}_3
\end{aligned} \tag{3}
$$

A tactical example, at certain time we measure the start and end of the segment. Measuring start of the segment will be our first spacetime coordinate $e_1$, measuring end segment will be our second spacetime coordinate $e_2$. Later we measure the same segment and get $e_3$ and $e_4$. Obviously the physical meaning of separation here is the length of segment, so $(e_1, e_2)$ and $(e_3, e_4)$ has the same separation.

Now in a different coordinate, the segment was again measured twice, then separation of events $(e^{\prime}_1, e^{\prime}_2)$ and separation of events $(e^{\prime}_3, e^{\prime}_4)$ will still be the same.

Suppose
$$
\begin{aligned}
e_1 = (x,t), \qquad e_2 = (x + a, t + b)
\\
e_3 = (y, s), \qquad e_4 = (y + a, s + b)
\end{aligned} \tag{4}
$$
Only considering the first component and combining (1), (3), (4), we have
$$
\begin{aligned}
f(y+a, s+b) - f(y, s) = f(x+a, t+b) - f(x,t)
\end{aligned} \tag{5}
$$
Equation (5) is profound, it means the separation of two points only relies on $(a,b)$, irrelevant from the variable from $f$. Thus
$$
\begin{aligned}
f(x+a, t+b) = f(x,t) + g(a, b)
\end{aligned} \tag{6}
$$
Taking partial derivative of $x$ from both sides of (6),
$$
\begin{aligned}
\frac{\partial f}{\partial x}(x+a, t+b) = \frac{\partial f}{\partial x}(x, t)
\end{aligned} \tag{7}
$$
(6) is true for any choise of $(a, b)$, meaning it is a constant, $f$ is a linear function of x. Same derivation applied for t, so we can rewrite (1) to be
$$
\begin{aligned}
x^{\prime} = f(x, t) = A\cdot x + B \cdot t + E_1
\\
t^{\prime} = C\cdot x + D \cdot t + E_2
\end{aligned} \tag{8}
$$
The event $(x, t) = (0, 0)$ is where the origins coincide, and by convention that event is also $(x^{\prime}, t^{\prime}) = (0, 0)$. This gives $E_1 = E_2 = 0$. The transformation is
$$
\begin{aligned}
x^{\prime} = A\cdot x + B \cdot t
\\
t^{\prime} = C\cdot x + D \cdot t
\end{aligned} \tag{9}
$$
In other words, for two inertial systems, their coordinate transformation is just a linear transformation.

#### 2.3.1 compute the linear coefficients

### Proper time
Time is relative. Thus, different observers will have their different time $t^{\prime}$ thus disagree on each other. However, all observers must agree on one time: the time measured by a clock carried along the object's own worldline. Between two events on that worldline, the clock ticks a definite number of times, and a count of ticks is the same no matter who is watching. This is the object's proper time $\tau$.

### Conclusion 1: we all move at speed of light

## 3. Geodesics and Christoffel Symbols

## 4. Metric Tensor

## 5. Curvature of the spacetime

## 6. Energy fluxes and Einstein Equation

## 7. Practical problems and Simulation of Sagittarius A*
