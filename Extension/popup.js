const button = document.getElementById("analyzeBtn")

button.addEventListener("click", async () => {

  const [tab] = await chrome.tabs.query({
    active: true,
    currentWindow: true
  })

  chrome.tabs.sendMessage(
    tab.id,
    { action: "extractListing" },

    async (response) => {

      console.log("LISTING:", response)

      const jsonData = JSON.stringify(
        response,
        null,
        2
      )

      await navigator.clipboard.writeText(
        jsonData
      )

      alert(
        "Listing data copied to clipboard!"
      )
    }
  )
})