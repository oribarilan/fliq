# Getting Started

## The Curious Case of Developer Dave

Meet Dave 🙋‍♂️ . Dave is a developer 👨‍💻 . One day, Dave's boss asked him to write a program to manipulate massive list of customer data. 

Dave was excited 😃 He started writing the program right away. 

```python
customers = get_huge_list_of_customers()
active_customers = [ac for ac in customers if ac.is_active]
sorted_customers = sorted(active_customers, key=lambda c: c.last_purchase_date, reverse=True)
top_customers = sorted_customers[:100]
```