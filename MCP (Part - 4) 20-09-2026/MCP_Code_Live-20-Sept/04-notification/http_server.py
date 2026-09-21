import asyncio
from fastmcp import Context, FastMCP

mcp = FastMCP("Notification Server (HTTP)")


@mcp.tool
async def do_work(ctx: Context) -> str:
    """Do a slow job in 3 steps and report progress along the way."""

    for step in range(1, 4):
        await asyncio.sleep(1)  # pretend each step takes 1 second

        # Notification 1: a log message.
        await ctx.info(f"Finished step {step}")

        # Notification 2: a progress update (progress out of total),
        # with a short text message that goes along with it.
        await ctx.report_progress(progress=step, total=3, message=f"Step {step} is done")

    # The normal answer. It arrives LAST, after all the notifications.
    return "Job done!"


if __name__ == "__main__":
    # The MCP endpoint is:  http://127.0.0.1:8001/mcp
    mcp.run(transport="http", host="127.0.0.1", port=8001)
