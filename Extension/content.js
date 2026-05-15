chrome.runtime.onMessage.addListener(

  (request, sender, sendResponse) => {

    try {

      // =========================
      // TITLE
      // =========================

      let title = ""

      const titleSelectors = [

        ".x-item-title__mainTitle",

        "#itemTitle",

        "h1"
      ]

      for (const selector of titleSelectors) {

        const element =
          document.querySelector(selector)

        if (
          element &&
          element.innerText
        ) {

          title =
            element.innerText.trim()

          break
        }
      }

      // CLEAN TITLE
      if (title) {

        title = title.replace(
          "Details about  ",
          ""
        )
      }

      // =========================
      // PRICE
      // =========================

      let price = ""

      const priceSelectors = [

        ".x-price-primary",

        ".display-price",

        ".x-bin-price__content"
      ]

      for (const selector of priceSelectors) {

        const element =
          document.querySelector(selector)

        if (
          element &&
          element.innerText
        ) {

          price =
            element.innerText.trim()

          break
        }
      }

      // =========================
      // MAIN IMAGES
      // =========================

      const imageUrls = []

      const galleryImages =
        document.querySelectorAll(
          '.ux-image-carousel-item img'
        )

      galleryImages.forEach(img => {

        try {

          let src =
            img.src || img.dataset.src

          if (!src) return

          // HIGH RES
          src = src.replace(
            /s-l\\d+/,
            "s-l1600"
          )

          // FILTER BAD IMAGES
          if (

            src.includes(
              "i.ebayimg.com"
            )

            &&

            !src.includes("thumbs")

            &&

            !src.includes("$_1")

            &&

            !src.includes("s-l64")

            &&

            !src.includes("s-l96")

            &&

            !imageUrls.includes(src)

          ) {

            imageUrls.push(src)
          }

        } catch (e) {

          console.log(
            "IMAGE ERROR",
            e
          )
        }
      })

      // LIMIT
      const finalImages =
        imageUrls.slice(0, 12)

      // =========================
      // DESCRIPTION
      // =========================

      let description = ""

      const metaDescription =
        document.querySelector(
          'meta[name="description"]'
        )

      if (
        metaDescription &&
        metaDescription.content
      ) {

        description =
          metaDescription.content
      }

      // =========================
      // DEBUG LOG
      // =========================

      console.log({

        title: title,

        price: price,

        image_urls: finalImages,

        description: description
      })

      // =========================
      // SEND RESPONSE
      // =========================

      sendResponse({

        title: title,

        price: price,

        image_urls: finalImages,

        description: description
      })

    } catch (error) {

      console.error(
        "CONTENT SCRIPT ERROR:",
        error
      )

      sendResponse({

        error: error.toString()
      })
    }

    return true
  }
)