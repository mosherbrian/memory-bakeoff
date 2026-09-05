from dispatch.queue import Queue

q = Queue()
q.push("a")
q.push("b")
assert q.pop() == "a", "A: ordinary order"
assert q.pop() == "b", "A: ordinary order"

q = Queue()
q.push("a")
q.push("b")
q.push("u1", urgent=True)
q.push("u2", urgent=True)
order = [q.pop(), q.pop(), q.pop(), q.pop()]
assert order == ["u1", "u2", "a", "b"], f"B: order -> {order}, expected ['u1','u2','a','b']"
print("VERIFIER OK")
