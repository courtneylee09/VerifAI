import asyncio
import httpx

async def simulate_buyer():
    url = "http://localhost:8000/verify?claim=Is Rihanna the founder of Fenty Beauty?"
    
    print(f"--- ATTEMPTING TO ACCESS ENDPOINT ---")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                print(" SUCCESS: Data received!")
                print(f"Result: {response.json()}")
            elif response.status_code == 402:
                print("  PAYMENT REQUIRED (402): The endpoint requires payment")
                print(f"Response: {response.text}")
            else:
                print(f" FAILED: Status code {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"  ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(simulate_buyer())
