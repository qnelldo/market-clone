<script>
import { getAuth, signInWithPopup, GoogleAuthProvider } from "firebase/auth";
  import { user$ } from "../store";

const provider = new GoogleAuthProvider();
const auth = getAuth();

const loginWithGoogle= async() => {
  try{
    const result = await signInWithPopup(auth, provider);

    const credential = GoogleAuthProvider.credentialFromResult(result);
    const token = credential.accessToken;
    const user = result.user;
    
    user$.set(user);
    localStorage.setItem("token", token);


  }catch(error){
    console.log(error)
  };
};


</script>

<div>
  {#if $user$}
  <div>{$user$?.displayName} 로그인됨 </div>
  {/if}
  <div> 로그인 페이지입니다 </div>
  <button class="login-btn" on:click={loginWithGoogle}>
    <img class="google-img"
    src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/1024px-Google_%22G%22_logo.svg.png" alt="">
    <div>Google로 로그인 하기</div>
    <div/>
  </button>
</div>

<style>

.login-btn{
  widows: 200px;
  height: 70px;
  border: 1px solid gray;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.google-img{
width: 20px;

}
</style>