import asyncio
import logging
from vanna_setup import get_vanna_agent

# Diagnostic Logger for Deployment
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')
logger = logging.getLogger("ClinicalSeeder")

from vanna import ToolCall, ToolResult

async def add_memory(memory, question: str, sql: str):
    """Helper to save a successful tool usage to memory."""
    # Final alignment for DemoAgentMemory signature in Vanna 2.0.2
    await memory.save_tool_usage(
        question=question,
        tool_name="run_sql",
        args={"sql": sql},
        context=None,
        success=True,
        metadata={"source": "manual_seed"}
    )

async def seed_agent_memory(agent=None):
    if agent is None:
        agent = get_vanna_agent()
    memory = agent.agent_memory

    print("Seeding localized agent memory (Page 10 categories)...")

    # 1. How many patients do we have?
    await add_memory(memory, "How many patients do we have?", "SELECT COUNT(*) AS total_patients FROM patients")

    # 2. List all doctors and their specializations
    await add_memory(memory, "List all doctors and their specializations.", "SELECT name, specialization FROM doctors")

    # 3. Show me appointments for last month
    await add_memory(memory, "Show me appointments for last month.", "SELECT * FROM appointments WHERE strftime('%Y-%m', appointment_date) = strftime('%Y-%m', 'now', '-1 month')")

    # 4. Which doctor has the most appointments?
    await add_memory(memory, "Which doctor has the most appointments?", "SELECT d.name, COUNT(a.id) AS app_count FROM doctors d JOIN appointments a ON d.id = a.doctor_id GROUP BY d.id ORDER BY app_count DESC LIMIT 1")

    # 5. What is the total revenue?
    await add_memory(memory, "What is the total revenue?", "SELECT SUM(total_amount) AS total_revenue FROM invoices")

    # 5b. Show me revenue in 2025 year
    await add_memory(memory, "Show me revenue in 2025 year.", "SELECT SUM(total_amount) AS revenue_2025 FROM invoices WHERE strftime('%Y', invoice_date) = '2025'")

    # 6. Show revenue by doctor
    await add_memory(memory, "Show revenue by doctor.", "SELECT d.name, SUM(i.total_amount) AS revenue FROM doctors d JOIN appointments a ON d.id = a.doctor_id JOIN invoices i ON a.patient_id = i.patient_id GROUP BY d.name ORDER BY revenue DESC")

    # 7. How many cancelled appointments last quarter?
    await add_memory(memory, "How many cancelled appointments last quarter?", "SELECT COUNT(*) FROM appointments WHERE status = 'Cancelled' AND appointment_date >= date('now', '-3 months')")

    # 8. Top 5 patients by spending
    await add_memory(memory, "Top 5 patients by spending.", "SELECT p.first_name, p.last_name, SUM(i.total_amount) AS total_spent FROM patients p JOIN invoices i ON p.id = i.patient_id GROUP BY p.id ORDER BY total_spent DESC LIMIT 5")

    # 9. Average treatment cost by specialization
    await add_memory(memory, "Average treatment cost by specialization.", "SELECT d.specialization, AVG(t.cost) FROM doctors d JOIN appointments a ON d.id = a.doctor_id JOIN treatments t ON a.id = t.appointment_id GROUP BY d.specialization")

    # 10. Show monthly appointment count for the past 6 months
    await add_memory(memory, "Show monthly appointment count for the past 6 months.", "SELECT strftime('%Y-%m', appointment_date) AS month, COUNT(*) FROM appointments WHERE appointment_date >= date('now', '-6 months') GROUP BY month ORDER BY month DESC")

    # 11. Which city has the most patients?
    await add_memory(memory, "Which city has the most patients?", "SELECT city, COUNT(*) AS patient_count FROM patients GROUP BY city ORDER BY patient_count DESC LIMIT 1")

    # 12. List patients who visited more than 3 times
    await add_memory(memory, "List patients who visited more than 3 times.", "SELECT p.first_name, p.last_name, COUNT(a.id) as visit_count FROM patients p JOIN appointments a ON p.id = a.patient_id GROUP BY p.id HAVING visit_count > 3")

    # 13. Show unpaid invoices
    await add_memory(memory, "Show unpaid invoices.", "SELECT * FROM invoices WHERE status IN ('Pending', 'Overdue')")

    # 14. What percentage of appointments are no-shows?
    await add_memory(memory, "What percentage of appointments are no-shows?", "SELECT (COUNT(CASE WHEN status = 'No-Show' THEN 1 END) * 100.0 / COUNT(*)) AS noshow_percentage FROM appointments")

    # 15. Show the busiest day of the week for appointments
    await add_memory(memory, "Show the busiest day of the week for appointments.", "SELECT strftime('%w', appointment_date) as day_of_week, COUNT(*) as app_count FROM appointments GROUP BY day_of_week ORDER BY app_count DESC LIMIT 1")

    # 16. Revenue trend by month
    await add_memory(memory, "Revenue trend by month.", "SELECT strftime('%Y-%m', invoice_date) AS month, SUM(total_amount) FROM invoices GROUP BY month ORDER BY month DESC")

    # 17. Average appointment duration by doctor
    await add_memory(memory, "Average appointment duration by doctor.", "SELECT d.name, AVG(t.duration_minutes) FROM doctors d JOIN appointments a ON d.id = a.doctor_id JOIN treatments t ON a.id = t.appointment_id GROUP BY d.name")

    # 18. List patients with overdue invoices
    await add_memory(memory, "List patients with overdue invoices.", "SELECT p.first_name, p.last_name, i.* FROM patients p JOIN invoices i ON p.id = i.patient_id WHERE i.status = 'Overdue'")

    # 19. Compare revenue between departments
    await add_memory(memory, "Compare revenue between departments.", "SELECT d.department, SUM(i.total_amount) AS revenue FROM doctors d JOIN appointments a ON d.id = a.doctor_id JOIN invoices i ON a.patient_id = i.patient_id GROUP BY d.department ORDER BY revenue DESC")

    # 20. Show patient registration trend by month
    await add_memory(memory, "Show patient registration trend by month.", "SELECT strftime('%Y-%m', registered_date) AS month, COUNT(*) FROM patients GROUP BY month ORDER BY month DESC")

    print("Memory seeding complete.")

if __name__ == "__main__":
    try:
        agent = get_vanna_agent()
        asyncio.run(seed_agent_memory(agent))
        
        # Note: In Vanna 2.x, training is handled via AgentMemory.save_tool_usage 
        # which is already called inside seed_agent_memory for all high-priority queries.
        
        logger.info("Agent Training Sync: Complete.")
    except Exception as e:
        logger.error(f"Seeding failure: {e}")
