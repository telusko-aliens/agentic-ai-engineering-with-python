
import asyncio
from fastmcp import Context, FastMCP

mcp = FastMCP("Notification Server")

@mcp.tool
async def do_work(ctx: Context) -> str:
    """Do a slow job in 3 steps and report progress along the way."""

    for step in range(1, 4):
        await asyncio.sleep(1)

        # Notification 1: a log message.
        await ctx.info(f"Finished step {step}")

        # Notification 2: a progress update (progress out of total),
        # with a short text message that goes along with it.
        await ctx.report_progress(progress=step, total=3, message=f"Step {step} is done")

    # The normal answer. It arrives LAST, after all the notifications.
    return "Job done!"

if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
