# MediQueue — Smart Hospital Patient Management System

A real-life DSA mini project built using Python Flask, HTML, CSS and JavaScript.

## DSA Concepts
1. Priority Queue (`heapq`) — Critical/High/Medium/Low cases.
2. Queue (`collections.deque`) — Normal patients are processed FIFO.
3. Searching — Patient ID, name, department and symptoms.
4. Sorting — Name, age and priority.

## Run
1. Install Python 3.
2. Open terminal in this folder.
3. Run:
   `pip install flask`
4. Run:
   `python app.py`
5. Open:
   `http://127.0.0.1:5000`

## Demo Flow
Register 3–5 patients with different priorities.
- Add one Critical patient.
- Add one Normal patient.
- Click "Call Next Patient".
The Critical patient is called first because the priority queue is checked before the normal FIFO queue.

