export type DiagnoseItem = {
    id: number;
    date: string;       // YYYY-MM-DD
    summary: string;    // 진단명
  };
  
  export type LikedItem = {
    id: number;
    brand: string;
    name: string;
    price: number;
    image: string;
    href: string;
  };
  
  export type UserProfile = {
    avatar: string;
    name: string;
    email: string;
    info: Array<{ label: string; value: string }>;
  };