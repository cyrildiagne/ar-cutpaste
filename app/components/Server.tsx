import Base64 from "./Base64";

const URL = "http://192.168.1.29:8080";

/**
 *class containing all the static functions used for the interaction with the server
 *
 * @export
 * @class Server
 */
export default class Server {

  /**
   *Transform array buffer to base64 string
   *
   * @param {ArrayBuffer} buffer
   * @returns {string}
   */
  public static arrayBufferToBase64(buffer: ArrayBuffer): string {
    let binary = "";
    const bytes = [].slice.call(new Uint8Array(buffer));
    for (const b of bytes) {
      binary += String.fromCharCode(b);
    }
    return Base64.btoa(binary);
  }

  public static ping(): void {
    fetch(URL + "/ping").catch((e) => console.error(e));
  }

  /**
   *generate the formData object that will be send to the server
   *
   * @param {string} imageURI
   * @returns {FormData}
   */
  public static generateFormData(imageURI: string): FormData {
    const formData = new FormData();
    formData.append("data", {
      uri: imageURI,
      name: "photo",
      type: "image/jpg",
    });
    return formData;
  }

  /**
   *cut and send the image
   *
   * @param {string} imageURI
   * @returns {Promise<string>}
   */
  public static async cut(imageURI: string): Promise<string> {
    const formData = this.generateFormData(imageURI);

    const res = await fetch(URL + "/cut", { method: "POST", body: formData })
    console.log("> converting...");
    const buffer = await res.arrayBuffer();
    const base64Flag = "data:image/png;base64,";
    const imageStr = this.arrayBufferToBase64(buffer);
    const resp = base64Flag + imageStr;

    return resp;
  }

  /**
   *paste the data from the server
   *
   * @param {string} imageURI
   * @returns {Promise<any>}
   */
  public static async paste(imageURI: string): Promise<any> {
    const formData = this.generateFormData(imageURI);
    const resp = await fetch(URL + "/paste", { method: "POST", body: formData });
    return resp.json();
  }
}
